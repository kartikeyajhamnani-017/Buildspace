package com.kartikeyajhamnani_017.nexus.inventory_service.messaging;

import org.springframework.amqp.core.Binding;
import org.springframework.amqp.core.BindingBuilder;
import org.springframework.amqp.core.Queue;
import org.springframework.amqp.core.TopicExchange;
import org.springframework.amqp.rabbit.config.RetryInterceptorBuilder;
import org.springframework.amqp.rabbit.config.SimpleRabbitListenerContainerFactory;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.retry.RejectAndDontRequeueRecoverer;
import org.springframework.amqp.support.converter.JacksonJsonMessageConverter;
import org.springframework.amqp.support.converter.MessageConverter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.aopalliance.aop.Advice;

@Configuration
public class RabbitMQConfig {

    public static final String EXCHANGE = "nexus.exchange";
    public static final String QUEUE = "inventory.order-placed.queue";
    public static final String ROUTING_KEY = "order.placed";

    @Bean
    public TopicExchange nexusExchange() {
        return new TopicExchange(EXCHANGE, true, false);
    }

    @Bean
    public Queue orderPlacedQueue() {
        return new Queue(QUEUE, true);
    }

    @Bean
    public Binding orderPlacedBinding(Queue orderPlacedQueue, TopicExchange nexusExchange) {
        return BindingBuilder.bind(orderPlacedQueue).to(nexusExchange).with(ROUTING_KEY);
    }

    @Bean
    public MessageConverter jsonMessageConverter() {
        return new JacksonJsonMessageConverter();
    }

    @Bean
    public SimpleRabbitListenerContainerFactory rabbitListenerContainerFactory(
            ConnectionFactory connectionFactory, MessageConverter jsonMessageConverter) {
        SimpleRabbitListenerContainerFactory factory = new SimpleRabbitListenerContainerFactory();
        factory.setConnectionFactory(connectionFactory);
        factory.setMessageConverter(jsonMessageConverter);
        // Manual ack: the listener only acks after a successful, committed stock update.
        factory.setAcknowledgeMode(org.springframework.amqp.core.AcknowledgeMode.MANUAL);
        // Retries transient failures (e.g. a momentary DB hiccup) a few times before
        // giving up; on final failure the message is rejected without requeue so a
        // single poison message can't loop forever (full DLQ handling is future work).
        Advice retryInterceptor = RetryInterceptorBuilder.stateless()
                .maxRetries(3)
                .backOffOptions(500, 2.0, 5000)
                .recoverer(new RejectAndDontRequeueRecoverer())
                .build();
        factory.setAdviceChain(retryInterceptor);
        return factory;
    }
}
